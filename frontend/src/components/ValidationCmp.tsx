export function ValidationCmp({ message }: { message: string | undefined }) {
  return <div className="invalid-feedback">{message}</div>;
}
