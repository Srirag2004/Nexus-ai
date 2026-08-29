import { PropsWithChildren } from "react";
import clsx from "clsx";

type PanelProps = PropsWithChildren<{
  title: string;
  description?: string;
  className?: string;
}>;

export function Panel({ title, description, className, children }: PanelProps) {
  return (
    <section className={clsx("panel-glow rounded-[1.75rem] border border-border/80 bg-panel/85 p-5 backdrop-blur-md md:p-6", className)}>
      <div className="mb-4">
        <h2 className="font-serif text-xl font-semibold tracking-tight">{title}</h2>
        {description ? <p className="mt-1 text-sm text-muted">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}
