(ifdd-model-operations)=
# Operations

## Publishing into the content repositories

```shell
just publish
```

The recipe builds the JSON-LD files and copies
`output/<service>/json-ld/` into the directory in
`IFDD_MODEL_<SERVICE>_TARGET`. It checks all three targets before it copies
anything, overwrites files it generated, and never deletes. Files in a
target that the model did not generate are listed and left as they are.
Committing and pushing in the content repositories is a separate step.

The services serve the files from their content directories; nothing else
has to be generated.

```{note}
**Not tested:** publishing into the content clones of running schema, type
and unit services, and how long their caches keep the previous files.
```

## Template updates

```shell
cruft update
```

`src/linkml`, `tests/reference` and `.env` are on the skip list and stay
as they are. New entries in `dotenv.dist` do not reach an existing `.env`;
copy them by hand. After an update run `just build` and `just test`.

## Removing a namespace

Delete its source file, run `just json accept`, and delete the generated
files in the content repositories by hand: `just publish` lists them but
never deletes.
