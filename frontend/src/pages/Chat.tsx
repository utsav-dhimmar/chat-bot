import { AIMessage, HumanMessage } from "@/components/chat/Message";
import { TEMP_CONVERSION } from "@/temp/data";
import { zodResolver } from "@hookform/resolvers/zod/src/zod.js";
import { Fragment } from "react";
import { useForm } from "react-hook-form";
import {
    redirect,
    useLoaderData,
    useNavigate,
    type LoaderFunctionArgs,
} from "react-router-dom";
import { z } from "zod";

const RouterParamSchema = z.object({
	conversationId: z.uuid("v4"),
});
type RouteParams = z.infer<typeof RouterParamSchema>;

export async function chatLoader({ params }: LoaderFunctionArgs) {
	const conversation_Id = params;

	try {
		const { conversationId } = RouterParamSchema.parse(conversation_Id);
		return { conversationId };
	} catch (e) {
		console.log(e);
		return redirect("/login");
	}
}
const MessageSchema = z.object({
	message: z.string().trim(),
});
type messageData = z.infer<typeof MessageSchema>;
export default function Chat() {
	const {
		register,
		handleSubmit,
		formState: { errors },
	} = useForm<messageData>({
		resolver: zodResolver(MessageSchema),
	});
	const navigate = useNavigate();
	const { conversationId } = useLoaderData<RouteParams>();

	return (
		// <div className="container">
		<div className=" d-flex justify-content-center align-items-center vh-100 bg-light">
			<div className="card shadow p-4">
				{/*<h2 className="text-center mb-4">Chat</h2>
					<p className="text-center">Chat ID: {conversationId}</p>*/}
				<div className="card-body overflow-auto">
					{/*<HumanMessage
							message="	Hello! How can I help you with your React
					project today?"
						/>
						<AIMessage
							message="I'm having trouble with Bootstrap validation
					classes."
						/>*/}

					{TEMP_CONVERSION.map(({ role, text }) => (
						<Fragment key={text}>
							{role === "HUMAN" && (
								<HumanMessage message={text} />
							)}
							{role === "AI" && <AIMessage message={text} />}
							{/*<AIMessage
									message="I'm having trouble with Bootstrap validation
							classes."
								/>*/}
						</Fragment>
					))}
				</div>
				<div className="card-footer text-muted d-flex justify-content-start align-items-center p-3">
					<input
						type="text"
						className={`form-control ${errors.message ? "is-invalid" : ""}`}
						placeholder="Type message..."
						{...register("message")}
					/>
					<button className="btn btn-primary ms-3">Send</button>

					{/* Validation Error Fix: Must be sibling to input */}
					{errors.message && (
						<div className="invalid-feedback d-block">
							{errors.message.message}
						</div>
					)}
				</div>
			</div>

			{TEMP_CONVERSION.map(() => null)}
		</div>
		// </div>
	);
}
