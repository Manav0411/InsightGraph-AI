"use client";

import { notFound } from "next/navigation";
import {
  Button,
  Card,
  Chip,
  SectionHeader,
  PageShell,
  PageHeader,
  SignalCard,
  TextInput,
} from "../../components/ui";

// Dev-only living reference for the design-system primitives. Not shipped.

function Row({ label, children }) {
  return (
    <div className="flex flex-col gap-3 py-6 border-t border-outline-variant/30">
      <span className="font-mono text-[11px] uppercase tracking-[0.12em] text-on-surface-variant">
        {label}
      </span>
      <div className="flex flex-wrap items-center gap-4">{children}</div>
    </div>
  );
}

export default function StyleGuide() {
  if (process.env.NODE_ENV === "production") notFound();

  return (
    <PageShell width="wide">
      <PageHeader
        title="Style guide"
        subtitle="Every design-system primitive in one place. Toggle the app theme to check both grounds. This route does not exist in production."
      />

      {/* Type scale */}
      <section className="mb-12">
        <SectionHeader
          eyebrow="type"
          title="Three faces, three jobs"
          description="Instrument Serif for display, Newsreader for reading, Spline Sans Mono for the machine voice and every piece of UI chrome."
        />
        <div className="mt-6 flex flex-col gap-2">
          <p className="font-display text-5xl leading-tight text-on-surface">
            Display — Instrument Serif <em>the twelve</em>
          </p>
          <p className="font-reader text-lg text-on-surface-variant max-w-[58ch]">
            Reader — Newsreader. A face built for running prose: the briefing body,
            FAQ answers, descriptions, anything you actually read a paragraph of.
          </p>
          <p className="font-mono text-sm text-on-surface-variant">
            mono — Spline Sans Mono · 02:14 retriever pulled 1,847 · SQI 61
          </p>
        </div>
      </section>

      {/* Buttons */}
      <section className="mb-4">
        <SectionHeader eyebrow="buttons" title="Button" />
        <Row label="variant">
          <Button variant="primary">Subscribe free</Button>
          <Button variant="outline">Preferences</Button>
          <Button variant="ghost">Skip for now</Button>
          <Button variant="subtle">Discard</Button>
          <Button variant="primary" disabled>
            Saving…
          </Button>
        </Row>
        <Row label="size">
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </Row>
      </section>

      {/* Cards */}
      <section className="mb-4">
        <SectionHeader eyebrow="surfaces" title="Card" />
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-5">
          <Card className="p-6">
            <p className="font-reader text-on-surface">default — elevated on the page ground</p>
          </Card>
          <Card variant="flat" className="p-6">
            <p className="font-reader text-on-surface">flat — quiet nested container</p>
          </Card>
          <Card variant="inset" className="p-6">
            <p className="font-mono text-sm">inset — the dark machine panel</p>
          </Card>
        </div>
        <div className="mt-5">
          <Card interactive as="div" className="p-6 max-w-sm">
            <p className="font-reader text-on-surface">interactive — hover for the lift</p>
          </Card>
        </div>
      </section>

      {/* Chips */}
      <section className="mb-4">
        <SectionHeader eyebrow="tokens" title="Chip" />
        <Row label="states">
          <Chip>foundation models</Chip>
          <Chip selected>ai agents</Chip>
          <Chip muted>crypto</Chip>
          <Chip selected onRemove={() => {}}>
            open source ai
          </Chip>
        </Row>
      </section>

      {/* SignalCard */}
      <section className="mb-4">
        <SectionHeader eyebrow="composite" title="SignalCard" />
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-5">
          <SignalCard
            kicker="top story · tavily"
            title="Nvidia buys Hugging Face in a $12.9B bet on open-source AI"
            summary="Consolidates the model-hosting layer under one vendor; the open commons now has a landlord."
            tags={["m&a", "open-source"]}
            trend={4.4}
            sqi={61}
          />
          <SignalCard
            kicker="research · arxiv cs.CL"
            title="Multi-step tool-calling over public APIs: a benchmark and a data recipe"
            summary="A new eval for agents that chain real API calls, plus a synthesis method for training data."
            onClick={() => {}}
          />
        </div>
      </section>

      {/* Inputs */}
      <section className="mb-4">
        <SectionHeader eyebrow="forms" title="TextInput" />
        <div className="mt-6 flex flex-col gap-4 max-w-sm">
          <TextInput icon="search" placeholder="Search topics, signals…" />
          <TextInput placeholder="Add a topic and press Enter…" />
        </div>
      </section>
    </PageShell>
  );
}
