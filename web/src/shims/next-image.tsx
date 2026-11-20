// Vite stand-in for next/image: renders a plain <img>.
import type { ImgHTMLAttributes } from "react";

type Props = ImgHTMLAttributes<HTMLImageElement> & {
  src: string;
  fill?: boolean;
  priority?: boolean;
  quality?: number;
  unoptimized?: boolean;
  placeholder?: string;
  blurDataURL?: string;
};

export default function Image({ fill, priority, quality, unoptimized, placeholder, blurDataURL, style, ...rest }: Props) {
  void quality; void unoptimized; void placeholder; void blurDataURL;
  return (
    <img
      loading={priority ? "eager" : "lazy"}
      style={fill ? { position: "absolute", inset: 0, width: "100%", height: "100%", ...style } : style}
      {...rest}
    />
  );
}
