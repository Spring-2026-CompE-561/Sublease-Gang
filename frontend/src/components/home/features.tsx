import { Shield, MapPin, Calendar } from "lucide-react";

const features = [
  {
    icon: Shield,
    title: "Verified Students",
    description: "All users verified with university email addresses",
    iconBg: "bg-pink-100 text-pink-600",
  },
  {
    icon: MapPin,
    title: "Near Campus",
    description: "Find housing close to your university and classes",
    iconBg: "bg-blue-100 text-blue-600",
  },
  {
    icon: Calendar,
    title: "Flexible Terms",
    description: "Short-term subleases perfect for summer and semester breaks",
    iconBg: "bg-green-100 text-green-600",
  },
];

export default function Features() {
  return (
    <section className="px-4 py-16">
      <div className="mx-auto max-w-6xl">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div key={feature.title} className="flex flex-col items-center text-center">
                <div className={`flex h-14 w-14 items-center justify-center rounded-full ${feature.iconBg}`}>
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="mt-4 font-semibold">{feature.title}</h3>
                <p className="mt-2 max-w-xs text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}