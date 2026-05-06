import { redirect } from "next/navigation";

export default function MapPage() {
	return redirect("/listings?view=map");
}
