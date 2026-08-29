import { PropsWithChildren } from "react";
import clsx from "clsx";

type PanelProps = PropsWithChildren<{
  title: string;
  description?: string;
  className?: string;
}>;

export function Panel({ title, description, className, children }: PanelProps) {
  return (
    <section className={clsx("rounded-3xl border border-border bg-panel/80 p-6", className)}>
      <div className="mb-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        {description ? <p className="mt-1 text-sm text-muted">{description}</p> : null}
      </div>
      {children}
    </section>
  );
}

