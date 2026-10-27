// Review-only foundation cut. This config cannot select a database target.
import { defineConfig } from "prisma/config";

export default defineConfig({ schema: "prisma/review/foundation-candidate.prisma" });
