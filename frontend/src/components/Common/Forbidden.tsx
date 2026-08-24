import { ShieldAlert } from "lucide-react"

/**
 * Shown in place of a page the current role may not see. Rendered inside the
 * app layout on purpose, so the sidebar stays available and the user can go
 * somewhere they do have access to.
 */
const Forbidden = () => {
  return (
    <div
      className="flex flex-col items-center justify-center text-center py-12"
      data-testid="forbidden"
    >
      <div className="rounded-full bg-muted p-4 mb-4">
        <ShieldAlert className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold">Access denied</h3>
      <p className="text-muted-foreground">
        You don't have permission to view this page.
      </p>
    </div>
  )
}

export default Forbidden
