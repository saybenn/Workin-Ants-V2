// Review-only: no datasource URL, environment loader, migrations or shadow database.
import { defineConfig } from "prisma/config";

export default defineConfig({ schema: "prisma/review/physical-candidate.prisma" });
