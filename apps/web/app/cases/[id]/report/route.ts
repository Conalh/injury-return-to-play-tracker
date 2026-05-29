import { getCaseReportPdf } from "@/lib/api-client";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const pdf = await getCaseReportPdf(id);
  // Strip anything outside a safe charset so the id cannot break out of the
  // quoted filename token and inject extra Content-Disposition parameters.
  const safeId = id.replace(/[^a-zA-Z0-9_-]/g, "");
  return new Response(pdf, {
    headers: {
      "content-disposition": `attachment; filename="return-play-${safeId}.pdf"`,
      "content-type": "application/pdf",
    },
  });
}
