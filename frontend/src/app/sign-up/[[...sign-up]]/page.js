import { SignUp } from "@clerk/nextjs";

export default function Page() {
  return (
    <div className="flex items-center justify-center h-full min-h-[70vh]">
      <SignUp forceRedirectUrl="/onboarding" fallbackRedirectUrl="/onboarding" />
    </div>
  );
}
