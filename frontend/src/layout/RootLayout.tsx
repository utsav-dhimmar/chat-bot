import { ChatHistory } from "@/components/ChatHistory";
import { Outlet } from "react-router-dom";

export default function RootLayout() {
	return (
		<>
			<nav>Navbar</nav>
			<ChatHistory />
			<Outlet />
		</>
	);
}
