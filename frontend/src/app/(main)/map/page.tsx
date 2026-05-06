import { redirect } from "next/navigation";

export default function MapPage() {
	redirect("/listings?view=map");
}
