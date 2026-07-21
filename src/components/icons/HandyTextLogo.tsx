/* eslint-disable i18next/no-literal-string -- decorative brand wordmark, not translatable */
import React from "react";

// Dictao wordmark: the lowercase monospace word "dictao" followed by a lime
// cursor block — the signature of the brand ("dictao█"). Keeps the original
// component name/props so existing imports (Sidebar, Onboarding,
// AccessibilityOnboarding) don't change. The letters use the neutral
// `logo-stroke` token (dark on light, light on dark); the cursor block uses the
// lime `logo-primary` token.
const HandyTextLogo = ({
  width,
  height,
  className,
}: {
  width?: number;
  height?: number;
  className?: string;
}) => {
  return (
    <svg
      width={width}
      height={height}
      className={className}
      viewBox="0 0 330 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="dictao"
      role="img"
    >
      <text
        x="8"
        y="75"
        fontFamily="'JetBrains Mono','Fira Code',ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"
        fontSize="72"
        fontWeight="700"
        letterSpacing="-2"
        className="logo-stroke"
      >
        dictao
      </text>
      {/* Cursor block — the lime signature. Sits just past the wordmark with a
          small deliberate gap, like a terminal caret. */}
      <rect
        x="284"
        y="17"
        width="36"
        height="60"
        rx="4"
        className="logo-primary"
      />
    </svg>
  );
};

export default HandyTextLogo;
