//! Layout names and pure geometry calculations for the tmux picker.

pub const LAYOUTS: [(&str, &str); 5] = [
    ("Side by side", "even-horizontal"),
    ("Stacked", "even-vertical"),
    ("Tiled", "tiled"),
    ("Tiled - big left", "tiled-left"),
    ("Tiled - big right", "tiled-right"),
];

/// Splits `total` cells into `count` parts, leaving one cell per border.
fn sizes(total: usize, count: usize) -> Vec<usize> {
    let usable = (total + 1).saturating_sub(count);
    let (base, extra) = (usable / count, usable % count);
    (0..count).map(|i| base + usize::from(i < extra)).collect()
}

/// Builds a tmux layout string with equal-width columns, where the columns
/// holding fewer (and so larger) panes sit on the requested side. Returns
/// `None` when the window is too small.
pub fn column_layout(
    width: usize,
    height: usize,
    panes: &[String],
    large_left: bool,
) -> Option<String> {
    let rows = (panes.len() - 1).isqrt() + 1;
    let columns = panes.len().div_ceil(rows);
    let mut counts = vec![rows; columns];
    counts[columns - 1] = panes.len() - rows * (columns - 1);
    if large_left {
        counts.reverse();
    }
    let widths = sizes(width, columns);
    let max_count = *counts.iter().max()?;
    if *widths.iter().min()? < 2 || *sizes(height, max_count).iter().min()? < 2 {
        return None;
    }
    let mut cells = Vec::with_capacity(columns);
    let (mut x, mut index) = (0, 0);
    for (&w, &count) in widths.iter().zip(&counts) {
        let mut leaves = Vec::with_capacity(count);
        let mut y = 0;
        for h in sizes(height, count) {
            leaves.push(format!("{w}x{h},{x},{y},{}", panes[index]));
            y += h + 1;
            index += 1;
        }
        cells.push(if count == 1 {
            leaves.swap_remove(0)
        } else {
            format!("{w}x{height},{x},0[{}]", leaves.join(","))
        });
        x += w + 1;
    }
    let body = if columns == 1 {
        cells.swap_remove(0)
    } else {
        format!("{width}x{height},0,0{{{}}}", cells.join(","))
    };
    let checksum = body.bytes().fold(0u32, |c, b| {
        (((c >> 1) | ((c & 1) << 15)) + u32::from(b)) & 0xffff
    });
    Some(format!("{checksum:04x},{body}"))
}
