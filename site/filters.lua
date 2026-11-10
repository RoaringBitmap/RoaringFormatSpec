-- Pandoc filter turning README.md into the GitHub Pages site.
--  * the first level-1 heading becomes the page title (shown in the hero);
--  * the hand-written table of contents is dropped (the site builds its own);
--  * images alone in a paragraph become figures with captions;
--  * relative links to repository files point to GitHub.

local REPO = "https://github.com/RoaringBitmap/RoaringFormatSpec"

local function is_toc_list(block)
  if block.t ~= "BulletList" then return false end
  local links, internal = 0, 0
  pandoc.walk_block(block, {
    Link = function(l)
      links = links + 1
      if l.target:match("^#") then internal = internal + 1 end
    end,
  })
  -- the table of contents is a list made only of internal links
  return links > 0 and links == internal
end

function Pandoc(doc)
  local blocks = pandoc.List()
  local seen_title = false
  for _, b in ipairs(doc.blocks) do
    if not seen_title and b.t == "Header" and b.level == 1 then
      seen_title = true
      doc.meta.pagetitle = pandoc.utils.stringify(b.content)
    elseif is_toc_list(b) then
      -- skip the manual table of contents
    elseif b.t == "Para"
        and pandoc.utils.stringify(b):find("roaringbitmap.github.io/RoaringFormatSpec", 1, true) then
      -- skip the README's pointer to this very site
    else
      blocks:insert(b)
    end
  end
  doc.blocks = blocks
  return doc
end

function Para(p)
  if #p.content == 1 and p.content[1].t == "Image" then
    local img = p.content[1]
    local caption = img.caption
    return pandoc.Figure(pandoc.Plain({ img }), { long = { pandoc.Plain(caption) } })
  end
end

function Link(l)
  local t = l.target
  if t:match("^%a[%w+.-]*:") or t:match("^#") or t:match("^figures/") then
    return nil
  end
  local kind = t:match("%.%w+$") and "blob" or "tree"
  l.target = REPO .. "/" .. kind .. "/master/" .. t
  return l
end
