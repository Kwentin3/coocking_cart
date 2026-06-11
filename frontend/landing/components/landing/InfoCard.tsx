import { Badge, Card, Icon, Stack } from "@/landing/components/primitives";
import type { IconKey } from "@/landing/registries/icon.registry";

type InfoCardProps = {
  title: string;
  description: string;
  iconKey: IconKey;
  badge?: string;
};

export function InfoCard({ title, description, iconKey, badge }: InfoCardProps) {
  return (
    <Card variant="default">
      <Stack gap="md">
        <span className="cardIcon">
          <Icon name={iconKey} variant="brand" decorative />
        </span>
        <Stack gap="xs">
          {badge ? <Badge variant="warning">{badge}</Badge> : null}
          <h3 className="cardTitle">{title}</h3>
          <p className="cardText">{description}</p>
        </Stack>
      </Stack>
    </Card>
  );
}
