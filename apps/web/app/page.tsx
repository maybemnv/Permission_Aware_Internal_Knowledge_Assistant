import { cookies } from "next/headers";
import { SearchWorkbench } from "@/components/SearchWorkbench";

export default async function HomePage() {
  const stored = (await cookies()).get("demo_principal")?.value;
  const initialPrincipal = stored === "allowed-user" || stored === "denied-user" || stored === "unmapped-user" || stored === "changed-group-user" || stored === "cross-tenant-user" || stored === "admin-user" ? stored : "allowed-user";
  return <SearchWorkbench initialPrincipal={initialPrincipal} />;
}