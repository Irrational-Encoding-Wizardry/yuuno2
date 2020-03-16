export interface Frame {
    metadata(): Promise<Map<string, string>>;
}
