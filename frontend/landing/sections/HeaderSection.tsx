import type { HeaderContent } from "@/landing/schemas";
import type { ResolvedLandingAction } from "@/landing/lib/actionVisibilityResolver";
import type { LandingActionId } from "@/landing/registries/cta.registry";
import type { LandingAnalyticsEvent } from "@/landing/registries/analytics.registry";
import { AssetImage, Button, Cluster, Container } from "@/landing/components/primitives";

type HeaderSectionProps = {
  content: HeaderContent;
  actions: Record<LandingActionId, ResolvedLandingAction>;
  navItemAnalyticsEvent: LandingAnalyticsEvent;
};

export function HeaderSection({ content, actions, navItemAnalyticsEvent }: HeaderSectionProps) {
  const loginAction = content.loginActionId ? actions[content.loginActionId] : undefined;

  return (
    <header className="siteHeader">
      <Container width="wide">
        <nav className="siteHeader__nav" aria-label="Основная навигация">
          <a className="siteHeader__brand" href="#hero" data-analytics-event={navItemAnalyticsEvent}>
            <span className="siteHeader__logo">
              <AssetImage assetKey={content.logoAssetKey} priority sizesToken="card" fit="contain" />
            </span>
            <span>{content.logoText}</span>
          </a>

          <div className="siteHeader__links">
            {content.navItems.map((item) => (
              <a key={item.id} href={item.href} data-analytics-event={navItemAnalyticsEvent}>
                {item.label}
              </a>
            ))}
          </div>

          <details className="siteHeader__menu">
            <summary>Меню</summary>
            <div className="siteHeader__menuPanel">
              {content.navItems.map((item) => (
                <a key={item.id} href={item.href} data-analytics-event={navItemAnalyticsEvent}>
                  {item.label}
                </a>
              ))}
              <div className="siteHeader__menuActions">
                {loginAction ? (
                  <Button action={loginAction} variant="ghost" size="sm" iconLeft="action.login" iconOnly ariaLabel="Вход в MVP" />
                ) : null}
              </div>
            </div>
          </details>

          <Cluster gap="sm" justify="end">
            {/* STICKY-MVP-ENTRY:
                Header MVP entry is an icon-only service action.
                It must not become a primary marketing CTA. */}
            {loginAction ? (
              <Button action={loginAction} variant="ghost" size="sm" iconLeft="action.login" iconOnly ariaLabel="Вход в MVP" />
            ) : null}
            <Button action={actions[content.primaryActionId]} variant="primary" size="sm" iconRight="action.arrowRight" />
          </Cluster>
        </nav>
      </Container>
    </header>
  );
}
