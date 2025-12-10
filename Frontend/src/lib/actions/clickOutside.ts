/**
 * Dispatch event on click outside of node
 */
export function clickOutside(node: HTMLElement, onEventFunction?: () => void) {
    const handleClick = (event: MouseEvent) => {
        if (node && !node.contains(event.target as Node) && !event.defaultPrevented) {
            if (onEventFunction) {
                onEventFunction();
            } else {
                node.dispatchEvent(new CustomEvent('click_outside', { detail: node }));
            }
        }
    };

    document.addEventListener('click', handleClick, true);

    return {
        destroy() {
            document.removeEventListener('click', handleClick, true);
        }
    };
}
