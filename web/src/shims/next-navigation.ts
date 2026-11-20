// Vite stand-in for next/navigation.
export function usePathname(): string {
  return typeof window === "undefined" ? "/" : window.location.pathname;
}
