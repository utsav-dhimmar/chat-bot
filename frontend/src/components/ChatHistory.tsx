import { Link, useNavigate } from "react-router-dom";
import { Button } from "./Button";

const TESTING_DATA = Array.from({ length: 10 }).map((_, index) => ({
	id: crypto.randomUUID(),
	title: `this is title ${index + 1}`,
}));

export function ChatHistory() {
	const navigate = useNavigate();
	return (
		<aside className="w-25 vh-100 overflow-auto  p-2 position-absolute z-2 ">
			<Button
				type="button"
				className="btn-info"
				onClick={_ => navigate("/new")}
			>
				New
			</Button>
			<ul className="list-group mt-2">
				{TESTING_DATA.map(({ id, title }) => (
					<li
						className="list-group-item list-group-item-action text-center"
						key={id}
					>
						<Link
							to={{
								pathname: `/chat/${id}`,
							}}
							className=""
						>
							{title}
						</Link>
					</li>
				))}
			</ul>
		</aside>
	);
}
