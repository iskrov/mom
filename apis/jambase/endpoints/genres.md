# Genres

## GET `/genres` - List Genres

Returns all available genres alphabetically. No parameters required.

**Response:**

```json
{
  "success": true,
  "genres": [
    { "slug": "bluegrass", "name": "Bluegrass" },
    { "slug": "blues", "name": "Blues" },
    ...
  ]
}
```

**Available genres:**

| Slug | Name |
|------|------|
| `bluegrass` | Bluegrass |
| `blues` | Blues |
| `christian` | Christian |
| `classical` | Classical |
| `country-music` | Country Music |
| `edm` | EDM |
| `folk` | Folk |
| `hip-hop-rap` | Hip-Hop/Rap |
| `indie` | Indie |
| `jamband` | Jamband |
| `jazz` | Jazz |
| `latin` | Latin |
| `metal` | Metal |
| `pop` | Pop |
| `punk` | Punk |
| `reggae` | Reggae |
| `rhythm-and-blues-soul` | R&B/Soul |
| `rock` | Rock |
