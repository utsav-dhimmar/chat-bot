import { Button, Input, ValidationCmp } from "@/components";
import { registerSchema, type RegisterFormData } from "@/schema/Auth";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";

export default function Register() {
	const navigate = useNavigate();
	const {
		register,
		handleSubmit,
		formState: { errors },
	} = useForm<RegisterFormData>({
		resolver: zodResolver(registerSchema),
	});

	const onSubmit = (data: RegisterFormData) => {
		console.log("Register:", data);
		navigate("/login");
	};

	return (
		<div className="d-flex justify-content-center align-items-center vh-100 bg-light">
			<div className="card shadow p-4" style={{ width: "400px" }}>
				<h2 className="text-center mb-4">Register</h2>
				<form onSubmit={handleSubmit(onSubmit)}>
					<div className="mb-3">
						<Input
							lable="Username"
							type="text"
							className={`form-control ${errors.username ? "is-invalid" : ""}`}
							{...register("username")}
							autoComplete="username webauthn"
						/>

						{errors.username && (
							<ValidationCmp message={errors.username.message} />
						)}
					</div>
					<div className="mb-3">
						<Input
							lable="Email"
							type="email"
							className={`form-control ${errors.username ? "is-invalid" : ""}`}
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
							className={`form-control ${errors.username ? "is-invalid" : ""}`}
							{...register("password")}
							autoComplete="new-password webauthn"
						/>

						{errors.password && (
							<ValidationCmp message={errors.password.message} />
						)}
					</div>
					<Button type="submit" className="btn-primary w-100">
						Register
					</Button>
				</form>
				<p className="text-center mt-3">
					Already have an account? <Link to="/login">Login</Link>
				</p>
			</div>
		</div>
	);
}
