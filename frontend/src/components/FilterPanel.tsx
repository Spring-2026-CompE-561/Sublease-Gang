"use client"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { DropdownMenu, 
         DropdownMenuContent, 
         DropdownMenuTrigger, 
         DropdownMenuRadioItem, 
         DropdownMenuRadioGroup } from "@/components/ui/dropdown-menu"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { useEffect, useState } from 'react'

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
  const [selectedRoomType, setSelectedRoomType] = useState<string>("");

  useEffect(() => {
    const fetchFilters = async () => {
      const res = await fetch("http://localhost:8000/api/v1/listings/filters")
      const data = await res.json()
      setFilterOptions(data)
    }
    fetchFilters()
  }, [])

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Price Range</h3>
        <Slider defaultValue={[0, 2000]} max={2000} step={50} />
        <div className="flex justify-between text-muted-foreground">
          <span>$0</span>
          <span>$2000</span>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Room Type</h3>
        <DropdownMenu>
          <DropdownMenuTrigger className="w-full border rounded-md px-4 py-2 text-left">
            {selectedRoomType || "Select Room Type"}
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuRadioGroup
              value={selectedRoomType}
              onValueChange={(value) => setSelectedRoomType(value)}
            >
              <DropdownMenuRadioItem value="">
                Any
              </DropdownMenuRadioItem>
              {filterOptions?.room_types.map((type) => (
                <DropdownMenuRadioItem key={type} value={type}>
                  {type}
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Amenities</h3>

        {["WiFi", "Furnished", "Utilities Included", "Parking", "Laundry", "Kitchen"].map(
          (item) => {
            const id = item.toLowerCase().replace(/\s+/g, "-")
            return (
              <div key={id} className="flex items-center space-x-3">
                <Checkbox id={id} />
                <Label htmlFor={id}>{item}</Label>
              </div>
            )
          }
        )}
      </div>
    </div>
  )
}

export function MobileFilterSheet() {
  return (
    <Sheet>
      <SheetTrigger className="sm:hidden">
        <Button variant="outline">Filters</Button>
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