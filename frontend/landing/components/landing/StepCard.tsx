import { Card, Icon, Stack } from "@/landing/components/primitives";
import type { IconKey } from "@/landing/registries/icon.registry";

type StepCardProps = {
  index: number;
  title: string;
  description: string;
  iconKey: IconKey;
};

export function StepCard({ index, title, description, iconKey }: StepCardProps) {
  return (
    <Card variant="soft">
      <Stack gap="md">
        <div className="stepCard__top">
          <span className="stepCard__index">{index}</span>
          <Icon name={iconKey} variant="brand" decorative />
        </div>
        <Stack gap="xs">
          <h3 className="cardTitle">{title}</h3>
          <p className="cardText">{description}</p>
        </Stack>
      </Stack>
    </Card>
  );
}
