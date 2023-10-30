import { QuestionMarkCircleIcon } from "@heroicons/react/24/outline";
import { useContext } from "react";
import { Id } from "../../components/id";
import { POPOVER_SIZE, PopOver } from "../../components/popover";
import { reduceArrays } from "../../utils/array";
import { Check } from "./checks/check";
import { DiffContext } from "./data-diff";

type tDataDiffConflictInfo = {
  path: string;
};

const getIdFromPath = (path: string = "") => {
  const id = path.split("/")?.[1];

  return id;
};

export const DataDiffConflictInfo = (props: tDataDiffConflictInfo) => {
  const { path } = props;

  const id = getIdFromPath(path);

  const { checksDictionnary } = useContext(DiffContext);

  if (!path || !checksDictionnary) {
    return null;
  }

  const keys = Object.keys(checksDictionnary);

  const matchingKeys = keys.filter((key: string) => key.startsWith(path));

  if (!matchingKeys.length) {
    return null;
  }

  const checks = matchingKeys
    .map((matchingKey: string) => checksDictionnary[matchingKey])
    .reduce(reduceArrays, []);

  const MoreButton = (
    <div className="p-1 cursor-pointer">
      <QuestionMarkCircleIcon className="h-5 w-5 text-custom-blue-green" aria-hidden="true" />
    </div>
  );

  const renderContent = () => {
    return (
      <div>
        <div className="flex items-center mb-2">
          <div className="mr-2">
            <Id id={id} />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {checks.map((check: any, index: number) => (
            <Check key={index} id={check?.id} />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="absolute right-0 font-normal">
      <div className="cursor-pointer">
        <PopOver buttonComponent={MoreButton} width={POPOVER_SIZE.LARGE} className="bg-gray-100">
          {renderContent}
        </PopOver>
      </div>
    </div>
  );
};
