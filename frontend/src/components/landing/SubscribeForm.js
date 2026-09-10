"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

/**
 * Email capture on the landing page. There is no separate mailing list —
 * the address is handed straight to the Clerk sign-up flow, which picks it
 * up from the `email_address` query param.
 */
export default function SubscribeForm({ onTerm = false, cta = "Start free" }) {
  const router = useRouter();
  const [email, setEmail] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = email.trim();
    router.push(
      trimmed
        ? `/sign-up?email_address=${encodeURIComponent(trimmed)}`
        : "/sign-up"
    );
  }

  return (
    <form
      className={`lp-signup${onTerm ? " lp-on-term" : ""}`}
      onSubmit={handleSubmit}
      aria-label="Subscribe"
    >
      <input
        type="email"
        placeholder="you@work.com"
        aria-label="Email address"
        autoComplete="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button className={`lp-btn${onTerm ? " lp-on-term" : ""}`} type="submit">
        {cta}
      </button>
    </form>
  );
}
