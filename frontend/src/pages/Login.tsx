import { Button, Input, ValidationCmp } from "@/components";
import { loginSchema, type LoginFormData } from "@/schema/Auth";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, type FieldErrors } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
	const navigate = useNavigate();
	const {
		register,
		handleSubmit,
		formState: { errors },
	} = useForm<LoginFormData>({
		resolver: zodResolver(loginSchema),
	});

	const onSubmit = (data: LoginFormData) => {
		console.log("Login:", data);
		navigate("/register");
	};

	const logErrors = (d: FieldErrors<{ email: string; password: string }>) => {
		console.log(d);
	};
	return (
		<div className="d-flex justify-content-center align-items-center vh-100 bg-light">
			<div className="card shadow p-4" style={{ width: "400px" }}>
				<h2 className="text-center mb-4">Login</h2>
				<form onSubmit={handleSubmit(onSubmit, logErrors)}>
					<div className="mb-3">
						<Input
							lable="Email"
							type="email"
							className={`form-control ${errors.email ? "is-invalid" : ""}`}
							{...register("email")}
							autoComplete="email webauthn"
						/>

						{errors.email && (
							<ValidationCmp message={errors.email.message} />
						)}
					</div>
					<div className="mb-3">
						<Input
							lable="Password"
							type="password"
							className={`form-control ${errors.password ? "is-invalid" : ""}`}
							{...register("password")}
							autoComplete="current-password webauthn"
						/>
						{errors.password && (
							<ValidationCmp message={errors.password.message} />
						)}
					</div>
					<Button type="submit" className="btn-primary w-100">
						Login
					</Button>
				</form>
				<p className="text-center mt-3">
					Don't have an account? <Link to="/register">Register</Link>
				</p>
			</div>
		</div>
	);
}
