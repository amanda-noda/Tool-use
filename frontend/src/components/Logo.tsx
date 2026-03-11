export function Logo({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="50%" stopColor="#a78bfa" />
          <stop offset="100%" stopColor="#4ade80" />
        </linearGradient>
      </defs>
      <path
        d="M12 34 L20 6 L28 34"
        stroke="url(#logoGrad)"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path
        d="M15 24 L25 24"
        stroke="url(#logoGrad)"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  )
}
