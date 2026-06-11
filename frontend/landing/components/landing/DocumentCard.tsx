import { Card, Icon, Stack } from "@/landing/components/primitives";
import type { IconKey } from "@/landing/registries/icon.registry";

type DocumentCardProps = {
  title: string;
  description: string;
  iconKey: IconKey;
};

export function DocumentCard({ title, description, iconKey }: DocumentCardProps) {
  return (
    <Card variant="document" density="compact">
      <Stack gap="sm">
        <Icon name={iconKey} variant="brand" decorative />
        <h3 className="cardTitle">{title}</h3>
        <p className="cardText">{description}</p>
      </Stack>
    </Card>
  );
}
