export function HumanMessage({ message }: { message: string }) {
  return (
    <div className="d-flex flex-row justify-content-end mb-4 ">
      <div
        className="p-3 me-3 border bg-secondary"
        style={{
          borderRadius: '15px',
        }}
      >
        <p className="small mb-0">{message}</p>
      </div>
    </div>
  );
}
export function AIMessage({ message }: { message: string }) {
  return (
    <div className="d-flex flex-row justify-content-start mb-4">
      <div
        className="p-3 ms-3 bg-info"
        style={{
          borderRadius: '15px',
        }}
      >
        <p className="small mb-0 text-break">{message}</p>
      </div>
    </div>
  );
}
