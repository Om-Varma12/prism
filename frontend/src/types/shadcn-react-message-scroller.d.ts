declare module '@shadcn/react/message-scroller' {
  import * as React from 'react';

  type MessageScrollerButtonDirection = 'start' | 'end';
  type MessageScrollerScrollAlign = 'start' | 'center' | 'end' | 'nearest';

  export type MessageScrollerScrollOptions = {
    align?: MessageScrollerScrollAlign;
    behavior?: ScrollBehavior;
    scrollMargin?: number;
  };

  export type MessageScrollerScrollable = {
    start: boolean;
    end: boolean;
  };

  export type MessageScrollerVisibilityState = {
    currentAnchorId: string | null;
    visibleMessageIds: string[];
  };

  type RenderState = Record<string, unknown>;
  type RenderFunction<TState extends RenderState> = (
    props: Record<string, unknown>,
    state: TState
  ) => React.ReactElement | null;
  type RenderProp<TState extends RenderState> = React.ReactElement | RenderFunction<TState>;

  type MessageScrollerButtonRenderState = {
    active: boolean;
    direction: MessageScrollerButtonDirection;
  };

  export const MessageScroller: {
    Provider: React.ComponentType<{
      children?: React.ReactNode;
      autoScroll?: boolean;
      defaultScrollPosition?: 'start' | 'end' | 'last-anchor';
      scrollEdgeThreshold?: number;
      scrollPreviousItemPeek?: number;
      scrollMargin?: number;
    }>;
    Root: React.ComponentType<React.ComponentProps<'div'>>;
    Viewport: React.ComponentType<
      React.ComponentProps<'div'> & {
        preserveScrollOnPrepend?: boolean;
      }
    >;
    Content: React.ComponentType<
      React.ComponentProps<'div'> & {
        spacerClassName?: string;
      }
    >;
    Item: React.ComponentType<
      React.ComponentProps<'div'> & {
        messageId?: string;
        scrollAnchor?: boolean;
      }
    >;
    Button: React.ComponentType<
      React.ComponentProps<'button'> & {
        behavior?: ScrollBehavior;
        direction?: MessageScrollerButtonDirection;
        render?: RenderProp<MessageScrollerButtonRenderState>;
      }
    >;
  };

  export function useMessageScroller(): {
    scrollToEnd: (options?: MessageScrollerScrollOptions) => boolean;
    scrollToMessage: (messageId: string, options?: MessageScrollerScrollOptions) => boolean;
    scrollToStart: (options?: MessageScrollerScrollOptions) => boolean;
  };

  export function useMessageScrollerScrollable(): MessageScrollerScrollable;
  export function useMessageScrollerVisibility(): MessageScrollerVisibilityState;
}
