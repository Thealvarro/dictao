// Dictao isotype: a thick rounded chevron (">") followed by a four-bar
// waveform — the "prompt + voice" mark. Heights step medium → high → max →
// low, with the last bar set slightly apart like a cursor. Kept monochrome
// (inherits fill/stroke from the text color, same as the surrounding sidebar
// icons) so it stays legible on the orange active-item background. Same export
// name, square viewBox, and { width, height } interface as before.
const HandyHand = ({
  width,
  height,
}: {
  width?: number | string;
  height?: number | string;
}) => (
  <svg
    width={width || 24}
    height={height || 24}
    viewBox="0 0 24 24"
    className="fill-text stroke-text"
    xmlns="http://www.w3.org/2000/svg"
  >
    {/* Chevron ">" — stroke only */}
    <path
      d="M6 7 L11 12 L6 17"
      fill="none"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    {/* Waveform bars — filled pills, heights vary; last one nudged right */}
    <rect x="13.2" y="8" width="1.8" height="8" rx="0.9" stroke="none" />
    <rect x="15.8" y="6" width="1.8" height="12" rx="0.9" stroke="none" />
    <rect x="18.4" y="4" width="1.8" height="16" rx="0.9" stroke="none" />
    <rect x="21.6" y="9" width="1.8" height="6" rx="0.9" stroke="none" />
  </svg>
);

export default HandyHand;
