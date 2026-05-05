"use client"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter 
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import {
  Combobox,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxInput,
  ComboboxItem,
  ComboboxList,
} from "@/components/ui/combobox"
import { Slider } from "@/components/ui/slider"
import { useEffect, useState } from 'react'
import { API_BASE_URL } from "@/lib/api"

type FilterOptions = {
  room_types: string[]
  colleges: { id: number; name: number }[]
  price_min: number
  price_max: number
  sqft_min: number
  sqft_max: number
}

export function FilterPanel() {
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [, setSelectedRoomType] = useState<string>("");
  const [, setSelectedCollege] = useState<string>("");
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 2000]);
  const [sqftRange, setSqftRange] = useState<[number, number]>([0, 2000]);

  const collegeNames = filterOptions?.colleges.map((c) => String(c.name)) ?? []
  const roomTypeList = filterOptions?.room_types ?? []

  useEffect(() => {
    const fetchFilters = async () => {
      const res = await fetch(`${API_BASE_URL}/api/v1/listings/filters`)
      const data = await res.json()
      setFilterOptions(data)
    }
    fetchFilters()
  }, [])

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">University</h3>
        <Combobox items={collegeNames} onValueChange={(value) => setSelectedCollege(value as string)}>
          <ComboboxInput placeholder="Search college..." />
          <ComboboxContent>
            <ComboboxEmpty>No college found.</ComboboxEmpty>
            <ComboboxList>
              {(item) => (
                <ComboboxItem key={item} value={item}>
                  {item}
                </ComboboxItem>
              )}
            </ComboboxList>
          </ComboboxContent>
        </Combobox>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Room Type</h3>
        <Combobox items={roomTypeList} onValueChange={(value) => setSelectedRoomType(value as string)}>
          <ComboboxInput placeholder="Select room type..." />
          <ComboboxContent>
            <ComboboxEmpty>No room types found.</ComboboxEmpty>
            <ComboboxList>
              {(item) => (
                <ComboboxItem key={item} value={item}>
                  {item}
                </ComboboxItem>
              )}
            </ComboboxList>
          </ComboboxContent>
        </Combobox>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Price Range</h3>
        <Slider defaultValue={[filterOptions?.price_min ?? 0, filterOptions?.price_max ?? 2000]}
          min={filterOptions?.price_min ?? 0}
          max={filterOptions?.price_max ?? 2000}
          step={50} 
          onValueChange={(value) => setPriceRange(value as [number, number])}
        />
        <div className="flex justify-between text-muted-foreground">
          <span>${priceRange[0]}</span>
          <span>${priceRange[1]}</span>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Square Footage</h3>
        <Slider defaultValue={[filterOptions?.sqft_min ?? 0, filterOptions?.sqft_max ?? 2000]}
          min={filterOptions?.sqft_min ?? 0}
          max={filterOptions?.sqft_max ?? 2000}
          step={50} 
          onValueChange={(value) => setSqftRange(value as [number, number])}
        />
        <div className="flex justify-between text-muted-foreground">
          <span>{sqftRange[0]} sq ft</span>
          <span>{sqftRange[1]} sq ft</span>
        </div>
      </div>
    </div>
  )
}

export function MobileFilterSheet() {
  return (
    <Sheet>
      <SheetTrigger className="sm:hidden inline-flex items-center justify-center rounded-xl border border-input bg-background px-4 py-2 text-sm font-medium shadow-sm hover:bg-accent hover:text-accent-foreground">
        Filters
      </SheetTrigger>

      <SheetContent side="left" className="w-[320px] sm:w-[380px] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Filters</SheetTitle>
        </SheetHeader>

        <div className="py-6">
          <FilterPanel />
        </div>

        <SheetFooter className="mt-6 flex-row gap-2 sm:justify-between">
          <Button variant="outline" className="flex-1">
            Reset
          </Button>
          <Button className="flex-1">Apply Filters</Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}