// Vite stand-in for next/link: renders a plain <a>.
import type { AnchorHTMLAttributes } from "react";

type Props = AnchorHTMLAttributes<HTMLAnchorElement> & { href: string; prefetch?: boolean; replace?: boolean; scroll?: boolean };

export default function Link({ prefetch, replace, scroll, ...rest }: Props) {
  void prefetch; void replace; void scroll;
  return <a {...rest} />;
}
