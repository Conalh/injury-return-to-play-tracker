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
    <main className="rp-form-page">
      <header className="rp-form-page-header">
        <Link href="/cases/new" className="rp-back-link">
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          Case creation
        </Link>
        <p className="rp-form-kicker">Athlete administration</p>
        <h1>Edit athlete</h1>
      </header>
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
