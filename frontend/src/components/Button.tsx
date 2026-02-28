type ButtonProps = {} & React.DetailedHTMLProps<
  React.ButtonHTMLAttributes<HTMLButtonElement>,
  HTMLButtonElement
>;

export function Button(props: ButtonProps) {
  const { className = '', ...restOfthe } = props;
  return <button className={`btn ${className}`} {...restOfthe}></button>;
}
