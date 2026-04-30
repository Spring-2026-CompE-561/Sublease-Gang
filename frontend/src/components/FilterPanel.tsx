import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import {
  ToggleGroup,
  ToggleGroupItem,
} from "@/components/ui/toggle-group"

export function FilterPanel() {
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
        <h3 className="text-lg font-semibold">Bedrooms</h3>
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
      <SheetTrigger>
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