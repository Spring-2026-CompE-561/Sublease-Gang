type Props = {
	params: Promise<{ id: string }>;
};

export default async function Listing({ params }: Props) {
	const { id } = await params;

	return (
		<main>
			<h1>Listing #{id}</h1>
			<p>Details for this listing will go here once the API is wired up.</p>
		</main>
	);
}
