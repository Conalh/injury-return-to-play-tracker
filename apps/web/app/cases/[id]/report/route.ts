import { getCaseReportPdf } from "@/lib/api-client";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const pdf = await getCaseReportPdf(id);
  return new Response(pdf, {
    headers: {
      "content-disposition": `attachment; filename="return-play-${id}.pdf"`,
      "content-type": "application/pdf",
    },
  });
}
