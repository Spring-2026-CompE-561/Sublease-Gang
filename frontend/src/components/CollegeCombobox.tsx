"use client";

import  { useState, useEffect } from "react";
import { Combobox, ComboboxContent, ComboboxInput, ComboboxItem, ComboboxList, ComboboxEmpty } from "@/components/ui/combobox";
import { College } from "@/types/college";
import { fetchApiJson } from "@/lib/api";

type CollegeComboboxProps = {
    value: string;
    onChange: (value: string) => void;
    invalid?: boolean;
};

export function CollegeCombobox({ value, onChange, invalid }: CollegeComboboxProps) {
	const [colleges, setColleges] = useState<College[]>([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		fetchApiJson<College[]>("/api/v1/colleges/")
			.then(setColleges)
			.finally(() => setLoading(false));
	}, []);

	const items = colleges.map((c) => `${c.id}::${c.name}`);
    const defaultValue = value ? items.find((item) => item.startsWith(`${value}::`)) ?? "" : "";

	return (
		<Combobox items={items} defaultValue={defaultValue} onValueChange={(val) => { if (val) onChange(val.split("::")[0]); }}>
			<ComboboxInput
				placeholder={loading ? "Loading colleges…" : "Search colleges…"}
				disabled={loading}
				aria-invalid={invalid}
			/>
			<ComboboxContent>
				<ComboboxEmpty>No colleges found.</ComboboxEmpty>
				<ComboboxList>
					{(item) => {
                        const [id, name] = item.split("::");
                        return (
						<ComboboxItem key={item} value={item}>
							{item.split("::")[1]}
						</ComboboxItem>
                        );
                    }}
				</ComboboxList>
			</ComboboxContent>
		</Combobox>
	);
}