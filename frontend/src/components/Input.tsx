import { useId } from "react";

type InputProps = {
	lable: string;
} & React.DetailedHTMLProps<
	React.InputHTMLAttributes<HTMLInputElement>,
	HTMLInputElement
>;

export function Input(props: InputProps) {
	const { lable, className, ...restOfInputProps } = props;
	const id = useId();
	return (
		<>
			<label htmlFor={id} className="form-label">
				{lable}
			</label>
			<input id={id} className={className} {...restOfInputProps} />
		</>
	);
}
