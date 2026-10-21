use crate::settings::SoundTheme;
use crate::settings::{self, AppSettings};
use cpal::traits::{DeviceTrait, HostTrait};
use log::{debug, error, warn};
use rodio::{OutputStream, OutputStreamBuilder};
use std::io::Cursor;
use std::path::{Path, PathBuf};
use std::sync::mpsc::{self, RecvTimeoutError};
use std::sync::OnceLock;
use std::thread;
use std::time::{Duration, Instant};
use tauri::{AppHandle, Manager};

pub enum SoundType {
    Start,
    Stop,
}

fn resolve_sound_path(
    app: &AppHandle,
    settings: &AppSettings,
    sound_type: SoundType,
) -> Option<PathBuf> {
    let sound_file = get_sound_path(settings, sound_type);
    let base_dir = get_sound_base_dir(settings);
    match base_dir {
        tauri::path::BaseDirectory::AppData => {
            crate::portable::resolve_app_data(app, &sound_file).ok()
        }
        _ => app.path().resolve(&sound_file, base_dir).ok(),
    }
}

fn get_sound_path(settings: &AppSettings, sound_type: SoundType) -> String {
    match (settings.sound_theme, sound_type) {
        (SoundTheme::Custom, SoundType::Start) => "custom_start.wav".to_string(),
        (SoundTheme::Custom, SoundType::Stop) => "custom_stop.wav".to_string(),
        (_, SoundType::Start) => settings.sound_theme.to_start_path(),
        (_, SoundType::Stop) => settings.sound_theme.to_stop_path(),
    }
}

fn get_sound_base_dir(settings: &AppSettings) -> tauri::path::BaseDirectory {
    match settings.sound_theme {
        SoundTheme::Custom => tauri::path::BaseDirectory::AppData,
        _ => tauri::path::BaseDirectory::Resource,
    }
}

pub fn play_feedback_sound(app: &AppHandle, sound_type: SoundType) {
    let settings = settings::get_settings(app);
    if !settings.audio_feedback {
        return;
    }
    if let Some(path) = resolve_sound_path(app, &settings, sound_type) {
        play_sound_async(app, path);
    }
}

pub fn play_feedback_sound_blocking(app: &AppHandle, sound_type: SoundType) {
    let settings = settings::get_settings(app);
    if !settings.audio_feedback {
        return;
    }
    if let Some(path) = resolve_sound_path(app, &settings, sound_type) {
        play_sound_blocking(app, &path);
    }
}

pub fn play_test_sound(app: &AppHandle, sound_type: SoundType) {
    let settings = settings::get_settings(app);
    if let Some(path) = resolve_sound_path(app, &settings, sound_type) {
        play_sound_blocking(app, &path);
    }
}

fn play_sound_async(app: &AppHandle, path: PathBuf) {
    send_to_player(app, path, None);
}

fn play_sound_blocking(app: &AppHandle, path: &Path) {
    let (done_tx, done_rx) = mpsc::channel();
    send_to_player(app, path.to_path_buf(), Some(done_tx));
    // Errors (or a dropped sender when playback fails) just end the wait.
    let _ = done_rx.recv();
}

/// How long the output stream stays open after the last cue. Opening an
/// output stream costs tens of ms, so keeping it warm across a dictation
/// (start cue -> stop cue) makes the stop cue instant. It still closes when
/// idle so we don't hold an audio session that can keep Windows from sleeping.
const STREAM_IDLE_TIMEOUT: Duration = Duration::from_secs(60);

/// Upper bound when waiting for a cue to finish, so a stream that dies
/// mid-playback can never hang the caller (and the mute that follows it).
const MAX_CUE_WAIT: Duration = Duration::from_secs(5);

struct PlayRequest {
    path: PathBuf,
    device: Option<String>,
    volume: f32,
    done: Option<mpsc::Sender<()>>,
}

fn send_to_player(app: &AppHandle, path: PathBuf, done: Option<mpsc::Sender<()>>) {
    static PLAYER: OnceLock<mpsc::Sender<PlayRequest>> = OnceLock::new();
    let player = PLAYER.get_or_init(|| {
        let (tx, rx) = mpsc::channel();
        thread::spawn(move || player_loop(rx));
        tx
    });

    let settings = settings::get_settings(app);
    let request = PlayRequest {
        path,
        device: settings.selected_output_device.clone(),
        volume: settings.audio_feedback_volume,
        done,
    };
    if player.send(request).is_err() {
        error!("Audio feedback player thread is gone");
    }
}

/// Owns the output stream for its whole life: cpal streams can't move between
/// threads, and reusing one is what removes the per-cue open latency.
fn player_loop(rx: mpsc::Receiver<PlayRequest>) {
    let mut stream: Option<(Option<String>, OutputStream)> = None;
    loop {
        let request = if stream.is_some() {
            match rx.recv_timeout(STREAM_IDLE_TIMEOUT) {
                Ok(request) => request,
                Err(RecvTimeoutError::Timeout) => {
                    debug!("Closing idle audio feedback stream");
                    stream = None;
                    continue;
                }
                Err(RecvTimeoutError::Disconnected) => return,
            }
        } else {
            match rx.recv() {
                Ok(request) => request,
                Err(_) => return,
            }
        };

        let path = request.path.clone();
        if let Err(e) = play_request(&mut stream, request) {
            error!("Failed to play sound '{}': {}", path.display(), e);
            // Reopen on the next cue in case the device went away.
            stream = None;
        }
    }
}

fn play_request(
    stream: &mut Option<(Option<String>, OutputStream)>,
    request: PlayRequest,
) -> Result<(), Box<dyn std::error::Error>> {
    let reusable = stream
        .as_ref()
        .is_some_and(|(device, _)| *device == request.device);
    if !reusable {
        // Release the old device before opening the new one.
        *stream = None;
        *stream = Some((
            request.device.clone(),
            open_output_stream(request.device.clone())?,
        ));
    }
    let Some((_, output)) = stream.as_ref() else {
        return Ok(());
    };

    let bytes = std::fs::read(&request.path)?;
    let sink = rodio::play(output.mixer(), Cursor::new(bytes))?;
    sink.set_volume(request.volume);

    match request.done {
        // Wait on a helper thread so a long start cue never delays the stop cue.
        Some(done) => {
            thread::spawn(move || {
                let deadline = Instant::now() + MAX_CUE_WAIT;
                while !sink.empty() && Instant::now() < deadline {
                    thread::sleep(Duration::from_millis(10));
                }
                let _ = done.send(());
            });
        }
        None => sink.detach(),
    }
    Ok(())
}

fn open_output_stream(
    selected_device: Option<String>,
) -> Result<OutputStream, Box<dyn std::error::Error>> {
    let stream_builder = if let Some(device_name) = selected_device {
        if device_name == "Default" {
            debug!("Using default device");
            OutputStreamBuilder::from_default_device()?
        } else {
            let host = crate::audio_toolkit::get_cpal_host();
            let devices = host.output_devices()?;

            let mut found_device = None;
            for device in devices {
                if device.name()? == device_name {
                    found_device = Some(device);
                    break;
                }
            }

            match found_device {
                Some(device) => OutputStreamBuilder::from_device(device)?,
                None => {
                    warn!("Device '{}' not found, using default device", device_name);
                    OutputStreamBuilder::from_default_device()?
                }
            }
        }
    } else {
        debug!("Using default device");
        OutputStreamBuilder::from_default_device()?
    };

    Ok(stream_builder.open_stream()?)
}
