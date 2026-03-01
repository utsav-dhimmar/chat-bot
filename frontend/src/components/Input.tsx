import { useId } from 'react';

type InputProps = {
  lable: string;
  error?: boolean;
} & React.DetailedHTMLProps<React.InputHTMLAttributes<HTMLInputElement>, HTMLInputElement>;

export function Input(props: InputProps) {
  const { lable, className, error, ...restOfInputProps } = props;
  const id = useId();
  const inputClassName = `${className || ''} ${error ? 'is-invalid' : ''}`.trim();

  return (
    <>
      <label htmlFor={id} className="form-label">
        {lable}
      </label>
      <input id={id} className={inputClassName} {...restOfInputProps} />
    </>
  );
}
