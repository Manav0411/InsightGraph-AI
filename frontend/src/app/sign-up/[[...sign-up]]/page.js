import { SignUp } from "@clerk/nextjs";

export default async function Page({ searchParams }) {
  // The landing page's email field hands the address over via `?email_address=`.
  const params = await searchParams;
  const raw = params?.email_address;
  const emailAddress = (Array.isArray(raw) ? raw[0] : raw)?.trim() || undefined;

  return (
    <div className="flex items-center justify-center h-full min-h-[70vh]">
      <SignUp
        forceRedirectUrl="/onboarding"
        fallbackRedirectUrl="/onboarding"
        initialValues={emailAddress ? { emailAddress } : undefined}
      />
    </div>
  );
}
