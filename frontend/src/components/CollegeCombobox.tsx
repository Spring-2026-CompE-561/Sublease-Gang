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

const items = colleges.map((c) => ({ id: String(c.id), name: c.name }));
const defaultValue = value
    ? colleges.find((c) => String(c.id) === value)?.name ?? ""
    : "";

return (
    <Combobox
        items={items.map((c) => c.name)}
        defaultValue={defaultValue}
        onValueChange={(val) => {
            if (val) {
                const match = colleges.find((c) => c.name === val);
                if (match) onChange(String(match.id));
            }
        }}
    >
        <ComboboxInput
            placeholder={loading ? "Loading colleges…" : "Search colleges…"}
            disabled={loading}
            aria-invalid={invalid}
        />
        <ComboboxContent>
            <ComboboxEmpty>No colleges found.</ComboboxEmpty>
            <ComboboxList>
                {(name) => (
                    <ComboboxItem key={name} value={name}>
                        {name}
                    </ComboboxItem>
                )}
            </ComboboxList>
        </ComboboxContent>
    </Combobox>
)};