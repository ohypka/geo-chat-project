import Link from "next/link";
import MapPage from "../components/Map/page";

export default function Page() {
  return (
    <div className="h-screen w-screen bg-neutral-950 text-neutral-100">
      <header className="flex items-center justify-between border-b border-neutral-800 bg-neutral-950/70 px-4 py-3 backdrop-blur">
        
        <Link
          href="/"
          title="Wróć do czatu"
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg hover:bg-neutral-800 transition"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-neutral-200"
          >
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </Link>

        <div className="text-xs text-neutral-400">
          Widok mapy
        </div>

        <div className="h-9 w-9" />
      </header>

      <div className="h-[calc(100vh-56px)]">
        <MapPage />
      </div>
    </div>
  );
}
