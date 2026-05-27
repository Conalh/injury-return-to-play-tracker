import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { ErrorState, UnauthorizedState } from "@/components/state-panels";
import { getCaseCreationData, UnauthorizedApiError } from "@/lib/api-client";
import { AthleteEditForm } from "./athlete-edit-form";

export default async function AthleteEditPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const data = await loadAthleteEditData(id);
  if (data.status === "unauthorized") {
    return <UnauthorizedState />;
  }
  if (data.status === "error" || !data.athlete) {
    return (
      <ErrorState
        title="Athlete unavailable"
        body="The athlete profile could not be loaded from the return-to-play API."
      />
    );
  }

  return (
    <main>
      <section className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <Link href="/cases/new" className="inline-flex min-h-10 items-center gap-2 text-sm font-semibold text-pine">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Case creation
        </Link>
        <div className="mt-5">
          <p className="text-sm font-semibold uppercase tracking-wide text-pine">Athlete administration</p>
          <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">Edit athlete</h1>
        </div>
      </section>
      <AthleteEditForm athlete={data.athlete} />
    </main>
  );
}

async function loadAthleteEditData(athleteId: string) {
  try {
    const data = await getCaseCreationData();
    return {
      status: "ok" as const,
      athlete: data.athletes.find((athlete) => athlete.id === athleteId) ?? null,
    };
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return { status: "unauthorized" as const, athlete: null };
    }
    return { status: "error" as const, athlete: null };
  }
}
