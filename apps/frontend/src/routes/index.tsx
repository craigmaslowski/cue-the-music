import { Navigate, createFileRoute } from '@tanstack/react-router';

/** Index route redirects to the crate (default view). */
export const Route = createFileRoute('/')({
  component: IndexRedirect,
});

function IndexRedirect() {
  return <Navigate to="/crate" />;
}
