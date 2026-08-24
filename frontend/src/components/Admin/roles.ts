import type { Role } from "@/client"

/**
 * Display metadata for the roles the API defines. These are labels only — what
 * each role may actually do is decided by the server. `satisfies` keeps this in
 * step with the generated `Role` union, so a role added or removed on the
 * backend fails the build here instead of silently going missing from the UI.
 */
export const ROLES = ["admin", "manager", "member"] as const satisfies Role[]

export const roleLabels: Record<Role, string> = {
  admin: "Admin",
  manager: "Manager",
  member: "Member",
}
